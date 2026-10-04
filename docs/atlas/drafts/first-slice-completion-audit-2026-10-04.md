# First HTTP slice completion audit

**Draft, 2026-10-04.** Read-only audit against FastAPI `0.141.1` commit
`95f8322ee1dcda7ceace7b1c4f6c9915b36d748f`, Starlette `1.6.0` oracle commit
`4f250d6b814587e20c5365f0a5f0c4d42bcb929f`, and the pinned Starlette-RS
contract commit `a345f8c3f5306dbc00c5fc37f8f16d2e79666065`. No tests or parity
commands were run and no active inputs were changed.

## Finding

`first-asgi-request.yaml` is a useful 12-case direct-`FastAPI.post` slice. Its
workload constructs one app with `title`, registers `POST /items/{item_id}`
with a request model, header dependency, optional query value, response model,
and status 201, then observes exact HTTP status/headers/body and ordered ASGI
send types. It also requests `/openapi.json` and selects the operation, ID,
parameters, request schema, and 201 response schema.

The smallest defensible completion is a **direct-route slice** with this
boundary: `FastAPI` construction → one POST registration → Starlette dispatch →
FastAPI request parsing/dependency solving/endpoint call → either validated JSON
serialization or a returned `Response`. The selected OpenAPI check can remain
as a companion assertion. This boundary does not establish the whole FastAPI
class surface or router-inclusion API.

## Existing coverage and reuse

| Behavior | Current evidence | Audit disposition |
|---|---|---|
| Successful POST, typed integer path, body model, aliased required header dependency, optional query default, response-model filtering, status 201 | `first-asgi-request` cases `create-item-valid` and `create-item-optional-query-default`; selected OpenAPI pointers | Covered as this workload's input design. The `first-asgi-request` workflow is not yet an `input_workflow_ref` for `FastAPI.__init__`, `FastAPI.post`, `FastAPI.__call__`, or `APIRoute.get_route_handler`; link the route evidence to those owners before using it as an operation support claim. `FastAPI.post` has a separate signature-probe ref. |
| Chunked JSON, malformed JSON, constrained/multi-field validation, JSON suffix, `text/plain`, absent Content-Type under strict default | Remaining first-slice cases; `request-body-media-type-upstream-v3` and `request-validation-error-details-wave` also cover adjacent parsing/error shapes | Do not add another generic request-media or 422 case. Keep first-slice claims to its exact wire projections. |
| Path miss (404), wrong method (405), invalid typed path | First workflow has 404 only. `routing-surface` already has 404, 405, and invalid path on an included GET route; `inherited-fastapi-add-route` has a wrong-method case for a Starlette route. | These are mapped adjacent cases, not the same direct POST registration. Add a same-path GET→405 case only if the direct slice explicitly claims method-miss dispatch; it is Starlette routing behavior under the pinned oracle. |
| Empty/missing required body | `request-body-tutorial-source-review-2026`, `tutorial-body001-source-review`, and body tutorial workflows already sample empty/missing bodies | No new case needed for generic required-body behavior; none is in the 12-case workload. |
| Response validation failure | `response-validation-error-focused` and `response-model-return-annotation-focused-upstream` cover invalid output and `ResponseValidationError` observations | Reuse and link these. Their selected direct error projections do not establish a composed HTTP 500 response. |
| Returned `Response` | `fastapi.response-model-return-annotation.response-passthrough` observes status, headers, and body; response tutorial cases also cover direct responses | This is adjacent coverage. It uses a return annotation that suppresses inferred response-model creation and does not observe ordered ASGI send types. Add at most one focused direct-route case if the slice must prove the `isinstance(raw_response, Response)` branch alongside an explicit `response_model`; compare status, ordered headers, bytes, and send types. FastAPI's branch is `routing.py:706-755`, especially `711-715`. |
| Router inclusion/body composition/response-class inheritance | `router-body-fields-composition-upstream`, `router-prefix-and-nested-composition-upstream`, `router-dependencies-isolated`, and `default-response-class-router-upstream` | These cover separate router behaviors. None is the same single included endpoint combining request model, response model, and endpoint result. Keep that as a separate router-composition slice if APIRouter inclusion is brought into scope. |

## Public signature and owner gaps

The first workload only supplies `title` to `FastAPI` and `response_model` plus
`status_code` to `post`. That is enough for its narrow input profile, not the
public signatures. Static comparison of the pinned source and PyO3 declarations
shows these uncovered options:

| Operation | Pinned FastAPI surface vs native binding | Smallest-slice impact |
|---|---|---|
| `FastAPI.post` | Source also accepts `description`, `callbacks`, `openapi_extra`, and `generate_unique_id_function`; the PyO3 signature omits them and orders the existing parameters differently (`applications.py` `post`; `application_runtime.rs:1532-1558`). | `operation-signatures-upstream` already probes `FastAPI.post`; `python.signature` is supported. Do not add a duplicate probe. A full-signature claim needs these omissions/order resolved or explicitly scoped. |
| `FastAPI.__init__` | Source also accepts `debug`, deprecated inherited `routes`, `openapi_tags`, `servers`, `swagger_ui_oauth2_redirect_url`, `openapi_prefix`, `root_path`, `root_path_in_servers`, `responses`, `callbacks`, `webhooks`, `deprecated`, `include_in_schema`, `swagger_ui_parameters`, `generate_unique_id_function`, and `separate_input_output_schemas` (`applications.py:58-94` and constructor signature). The native constructor does not expose them (`application_runtime.rs:1274-1304`). | `title` is the only constructor option used by this recipe. Manifest constructor signature parity is still unprobed; `routes` carries source deprecation evidence. |
| `FastAPI.include_router` and `APIRouter.include_router` | Source additionally accepts `responses`, `default_response_class`, `callbacks`, and `generate_unique_id_function` (`applications.py:1441-1614`; `routing.py:3133-3244`). Both native bindings expose only prefix/tags/dependencies/deprecated/include-in-schema (`application_runtime.rs:2211-2226`, `3487-3502`). | Out of the direct-route boundary; required before making a broad include-router signature claim. |
| `APIRouter.__init__` | Source additionally accepts `responses`, `callbacks`, deprecated inherited `routes`, `redirect_slashes`, `default`, `dependency_overrides_provider`, `route_class`, and `generate_unique_id_function` (`routing.py:2282-2519`). The native constructor omits these (`application_runtime.rs:3365-3429`). | Out of the direct-route boundary. Class-level APIRouter scope remains pending in the API manifest. |

The manifest has a direct target owner for `FastAPI.__call__` (`FastApiCall::finish_endpoint`), but `APIRoute.get_route_handler` still has a null `rust_binding`; connect that request/response plan to its actual native owner before claiming complete operation coverage. `FastAPI` and `APIRouter` class rows remain `scope-review-pending`. `route.match` and `dependency.call_order` selectors are **planned**; `validation.error_class` and `validation.error_details` are **partial**. The first workflow's exact HTTP and ASGI wire selectors are sufficient for its observed behavior, but cannot support claims about those internal records or call ordering.

## Minimal closure order

1. Define and record the boundary as one direct POST route, with selected
   OpenAPI output as a companion check; link its exact cases to constructor,
   decorator, ASGI-call, and route-handler manifest owners.
2. Reuse existing 404, 405, path-validation, body, response-validation, and
   router workflows rather than duplicating their generic cases. Add one
   explicit-response-model + direct-`Response` case with ASGI send observation
   only if this slice is intended to cover both endpoint return branches.
3. Keep full Python signature parity and router inclusion as separate contract
   work: the source/native option gaps above exceed this minimal workload.

The earlier `asgi-vertical-slice-review-2026-10-04.md` records a 12/12 parity
run after the pinned target revision was verified. This audit did not rerun it.
