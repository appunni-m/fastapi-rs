# Response-field traversal7: prospective mappings and admission checklist

2026-10-05. This is a temporary, read-only-repository plan. No active recipe,
workload, metadata, manifest, index, atlas, Rust or sibling file was changed.
No application/factory, live parity, compiler, installer or unit test ran.
Source contracts and static input review do not establish target support.

## Frozen independent inputs

Proposal directory: `/private/tmp/fastapi-rs-response-field-traversal-proposal-2026-10-05/`.
Independent review: `/private/tmp/fastapi-rs-response-field-traversal-independent-review-2026-10-05.md`.

| File | SHA256 |
| --- | --- |
| `response_field_traversal.py` | `35aa2d46026953a69ac6284f6a0215c62df22e19ddac0018c9d31336224de4d9` |
| `response-field-traversal.yaml` | `3dfd1caa6573faa55edaef83e1eb166e4279a97542bda323a4ea8ab2de929c66` |
| `review-plan.md` | `8d5164a0825cf7755f3049c905578dd264a2ad29609cc73a882785b9bffd8ad2` |

Future active recipe: `tests/fixtures/input-recipes/parity/response-field-traversal.yaml`.
Future active workload: `tests/fixtures/workloads/response_field_traversal.py`.
Future ignored materialization: `tests/fixtures/inputs/parity/response-field-traversal.json`.
Canonical binding is positional `create_app(factory_input, event_trace)`;
instantiate_per_case is true, schema is `fastapi-rs/python-asgi-workflow@9`.

All case IDs use prefix `fastapi.response-field-traversal.`. Preserve this order:

| Suffix | Actions | State reads | Other requests | Construction observations |
| --- | ---: | ---: | ---: | ---: |
| branch-second-construction-error-retry | 7 | 4 | 3 | 1 |
| parent-own-fields-before-child-traversal | 7 | 4 | 3 | 1 |
| earlier-full-direct-match-skips-later-include | 7 | 4 | 3 | 1 |
| earlier-partial-direct-match-reaches-later-full-include | 5 | 3 | 2 | 1 |
| unmatched-request-visits-both-includes | 6 | 3 | 3 | 1 |
| redirect-search-follows-initial-branch-traversal | 5 | 3 | 2 | 1 |
| returned-response-still-constructs-included-field | 5 | 3 | 2 | 1 |
| **Total** | **42** | **24** | **18** | **7** |

The seven cases are normal parity inputs, with no expected outputs or
normalization. Schema-hook refusal is a one-use ordinary user exception armed
only after setup. The routing tree, annotations and response-class declarations
remain fixed; this does not mean the hook itself is immutable or always succeeds.

## Proposed reviewed operation links

Append to `metadata.yaml:/reviewed_api_contract_overlay/operations`. Every row
already exists there. Each link is the future recipe path plus the complete
case_id, with no probe_id. Keep existing links, aliases and Rust bindings.

| Existing operation | Cases receiving new links | Links | Existing Rust binding suffix |
| --- | --- | ---: | --- |
| fastapi.applications.FastAPI.__init__ | all seven | 7 | application_runtime.rs::PyFastApi::new |
| fastapi.applications.FastAPI.__call__ | all seven | 7 | application_runtime.rs::FastApiCall::finish_endpoint |
| fastapi.applications.FastAPI.get | all seven: early /state; direct GET also in case3 | 7 | application_runtime.rs::PyFastApi::get |
| fastapi.APIRouter | all seven | 7 | application_runtime.rs::PyApiRouter::new |
| fastapi.routing.APIRouter.__init__ | all seven | 7 | application_runtime.rs::PyApiRouter::new |
| fastapi.routing.APIRouter.get | all seven | 7 | application_runtime.rs::PyOperationRouteDescriptor::__get__ |
| fastapi.applications.FastAPI.include_router | all seven | 7 | application_runtime.rs::PyFastApi::include_router |
| fastapi.applications.FastAPI.exception_handler | all seven register the public decorator; only case1 invokes this handler | 7 | application_runtime.rs::PyFastApi::exception_handler |
| fastapi.responses.JSONResponse | all seven state responses; selected error/returned-response paths also use it | 7 | application_runtime.rs::register |
| fastapi.routing.APIRouter.include_router | case2 parent-own-fields-before-child-traversal only | 1 | application_runtime.rs::PyApiRouter::include_router |
| fastapi.applications.FastAPI.post | case4 earlier-partial-direct-match-reaches-later-full-include only | 1 | application_runtime.rs::PyFastApi::post |
| **Total** | **11 existing operations** | **65** | |

All binding paths have prefix `fastapi-rs/src/`. Root APIRouter is its public
identity alias, so keep both its existing overlay and the canonical constructor
mapping. JSONResponse remains a direct sibling-owned re-export; these inputs
observe FastAPI field construction/selection through it and do not justify
changing that owner or claiming generic response parity.

Do not add mappings for add_api_route/api_route, router.post,
add_exception_handler, APIRoute, Default/DefaultPlaceholder, ModelField, OpenAPI,
url_path_for or WebSocket. The workload does not call those public operations or
probe private identities. Request.url/query_params accesses rely on the pinned
sibling public implementation; this proposal does not make a new Request alias
identity or complete Request behavior claim.

The direct `FastAPI.exception_handler` overlay already contains its pinned
source definition and handling-errors documentation evidence. The current
ordinary operation fixture validator resolves recipe/case/digests/selectors;
it does not require the inherited-operation documentation path intersection.
Thus the frozen recipe need not be edited to add handling-errors.md for this
mapping. Mapping inherited add_exception_handler instead would be both the
wrong directly exercised API and would introduce its separate stricter gate.
If a later atlas documentation mapping requires new recipe evidence, report
that exact requirement and review a separate input delta before changing hashes.

## Selectors and bounded descriptions

Each case actually selects this same catalog set:

- `http.status`, `http.headers.ordered`, `http.body.bytes`;
- `asgi.send.message_types`, `asgi.application_error.exception`;
- `construction.outcome`, `construction.exception_class`, `construction.exception_message`.

Append only missing selectors to the relevant operation union, preserving
existing selectors. A union describes all linked inputs, not proof that each
case establishes every selector. The canonical asgi_send observation alone
selects message types. Ordered warnings, schema/validation/serialization hooks,
handler records and **all prior non-state raw send fields** are retained through
the selected exact `/state` body. Do not claim a direct warnings.category_message
or validation.error_details/error.public_attributes selection for these seven.
Raw sends retain byte hex, tuple/list shape, headers, all keys and field presence;
state sends are excluded only from the recursive user journal and are still
canonically observed by the runner. Do not normalize more_body presence.

Keep existing feature IDs. `response-serialization` is a relevant addition to
nested APIRouter.include_router's existing feature union; `app-routing` and
`public-api-errors` already cover traversal and the handler. Do not add the
OpenAPI/WebSocket/worker features as evidence from these inputs.

Suggested appended supported_slice text for routing/field operations:

> Seven response-field-traversal normal inputs map fixed public route trees,
> a one-use user schema-hook refusal and retry, parent own-field preparation
> before child traversal, earlier full versus partial matches, misses, slash
> search and returned-Response field setup. They retain actual construction,
> callbacks, warnings/errors, exact status/ordered headers/body and full prior
> non-state send fields through an early public state route. Source-derived
> branch publication and traversal contracts require fresh identity-checked
> source/target receipts; these mappings do not establish complete target
> support, mutable router-version history or generic sibling behavior.

For exception_handler, explicitly limit invocation/error recovery to case1;
other six links establish registration within the declared route workflow.
For post, describe only the one earlier direct POST/later included GET case;
terminal 405 is not selected. For JSONResponse retain sibling ownership and
separate generic execution from the FastAPI field decision being observed.

Retain existing partial-contract target bindings and known gaps. If introducing
bindings on FastAPI.post, nested include_router or exception_handler, keep
FastAPI-RS ownership and partial-contract status; no target-complete status or
source-classification promotion follows. Suggested additional gap text:

- Visited included branches must prepare all own effective fields before
  publishing the vector, retry the whole unpublished branch after a later own
  constructor fails, descend into child branches only when matching reaches
  them, and retain successful fields across miss/redirect/handle paths. These
  seven inputs are a required fresh parity gate, not execution evidence.
- Route-version refresh/live additions, raw included-route proxies,
  URL/OpenAPI/WebSocket field traversal, empty-prefix validation traversal,
  reentrancy/concurrency, mutable model/default/metadata history, arbitrary
  schemas, terminal405, cancellation, streaming and worker scheduling remain
  outside this gate. The one-use user hook is not a native fault injection or
  proof of resource finalizer timing, yield cleanup or private cache identity.

Do not erase the existing lifecycle16/immutable-provenance gaps or infer broader
response-class precedence from traversal7, whose classes are omitted defaults
with ordinary returned JSONResponse controls. Internal DefaultPlaceholder and
ModelField classifications remain private/internal; they are source evidence.

## Pinned source evidence to append where relevant

FastAPI0.141.1 commit `95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`,
Starlette1.6.0 commit `4f250d6b814587e20c5365f0a5f0c4d42bcb929f`.
Target sibling source `/private/tmp/fastapi-rs-starlette-rs-b4c8a65`, commit
`b4c8a65c85e1b0d251ca05874412811eaa3ac7b8` only. Python3.12.13,
Pydantic2.13.4/core2.46.4 and AnyIO4.12.1 remain locked.

| Source evidence | Relevant source contract, not target support |
| --- | --- |
| fastapi/routing.py:1103-1114, symbol _populate_api_route_state; fastapi/utils.py:58-78, create_model_field; fastapi/_compat/v2.py:141-166, ModelField | Original declaration field construction; only PydanticSchemaGenerationError translated, ordinary user ValueError remains observable. |
| fastapi/routing.py:1599-1625, symbol _IncludedRouter | Own candidate local vector and publish-after-success; nested child represented without immediate materialization. The pinned source class is _IncludedRouter. |
| fastapi/routing.py:1730-1803, symbol _IncludedRouter | Match-driven child traversal and retained effective-context handling. |
| fastapi/routing.py:2719-2787, symbol APIRouter | Early full match, retained partial, initial scan before slash/default path. |
| fastapi/routing.py:3258-3312, symbol include_router | All proposed prefixes are nonempty, avoiding separate setup traversal. |
| fastapi/routing.py:711-748, symbol get_request_handler | Returned Response bypass follows matching and field setup. |
| tests/test_router_include_context.py; tests/test_router_redirect_slashes.py; tests/test_response_model_as_return_annotation.py | Existing public source contexts; no copied tests or expected outputs. |
| docs/en/docs/tutorial/bigger-applications.md; docs/en/docs/tutorial/response-model.md; docs/en/docs/advanced/response-directly.md | Recipe's reviewed public declaration/return contexts. |
| fastapi/applications.py:4729-4774, exception_handler; docs/en/docs/tutorial/handling-errors.md:82-102 | Existing decorator operation evidence; ordinary user schema error handled in case1. |
| Pinned Starlette middleware/exceptions.py:46-68 and _exception_handler.py:31-65 | Generic exception middleware/handler dispatch remains sibling-owned. |

Source references to private classes can be added under existing public operation
source_evidence without promoting those classes to reviewed public APIs.
Preserve current pins, root exports, alias identities and deprecation policy.

## Later admission checklist — requires separate authorization

1. After parent normal-restoration proof and permission to edit active inputs,
   verify the three frozen proposal hashes and independent review. Copy only
   the approved recipe/workload to the future active paths above. Preserve
   source evidence, positional factory, all seven cases, action order,
   unfiltered warnings and every raw send key. No oracle/comparator/policy edits.
2. Run canonical read_recipe and repository-configured Ruff lint/format static
   admission without importing the workload. Confirm 7 parity cases, 42 actions,
   7 construction observations, 24 state/18 non-state actions, unique case IDs,
   per-case action IDs and existence of pinned source-evidence paths. Do not
   claim these future checks already ran. The inactive author/reviewer static
   checks are distinct from active canonical admission.
3. Append the 65 precise fixture links above in reviewed metadata, add bounded
   descriptions/source evidence/selectors/gaps, then regenerate only required
   artifacts. Run sequentially with RUSTC_WRAPPER empty and the exact sibling:

```sh
RUSTC_WRAPPER= make parity-inputs STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
RUSTC_WRAPPER= make parity-index-update STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
RUSTC_WRAPPER= make compatibility-atlas-update STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
RUSTC_WRAPPER= make parity-validate PARITY_INPUT=tests/fixtures/inputs/parity/response-field-traversal.json STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
RUSTC_WRAPPER= make metadata-check api-contract-check python-facade-check rust-policy-check STARLETTE_RS_SOURCE=/private/tmp/fastapi-rs-starlette-rs-b4c8a65
```

   parity-inputs/index precede atlas generation; compatibility-atlas-update
   refreshes atlas/index/manifest and validates globally. Targeted validation
   follows so it reads a current manifest. Preserve any failed/stale generation
   diagnostic, resolve the cause, and rerun; do not weaken mappings or validators.
   Static checks are not builds or live app execution.
4. Report exact active input/workload/metadata/generated-artifact hashes,
   mappings/counts and every check; freeze all owned edits before parent runs
   pinned source7 and unchanged-target7 in isolated identity-checked processes.
   Retain constructor failures and any action-level not_run, even if case-level
   not_run is zero. Verify same recipe/workload/input/index/manifest case/action
   bindings with no skips/subsets/replayed or stored output substitutions.
5. Only separately authorized implementation may follow diagnostics. Later
   normal comparisons, regression selection and same-fixed-source coverage/fault
   receipts must retain distinct native/build identities. Equivalent benchmarks
   require appropriate parity gates; no speed or complete support claim is made
   by this checklist or by the prior immutable16 receipts.
