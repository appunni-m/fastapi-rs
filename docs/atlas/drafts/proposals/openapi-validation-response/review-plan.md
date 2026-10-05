# Inactive automatic validation-response proposal

Version 2, 2026-10-05. The original recipe, workload, plan and static receipt
were preserved under `v1/` and their frozen hashes checked before revision.
Original recipe SHA256 is
`3011a159d5f2bc478d14424e8c6854a1b0424078ef7551a0bda7f4480c36ed58`;
original plan SHA256 is
`309c07e962db543678a8d56c0fe4aa45ef630dde1cd1bdbf2ebc389756ea51b8`.
Workload remains byte-identical with SHA256
`9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130`.
Only runner warning selection and this plan's actual `FastAPI.__call__` mapping
were added; the request inputs and declared observation selectors are unchanged.

This is a prospective public-input gate, separate from the admitted retained
response-field three-case wave. It contains no expected output, normalization,
private route/cache access, backend detection or copied upstream test bodies.
Nothing is admitted or executed by this proposal.

## Inputs and counts

Future recipe: `tests/fixtures/input-recipes/parity/openapi-validation-response.yaml`.
Future workload: `tests/fixtures/workloads/openapi_validation_response.py`.
Both proposed files currently live only in this `/private/tmp` directory.

| Case ID suffix under `fastapi.openapi-validation-response.` | Independent input distinction |
|---|---|
| `automatic-after-declared-responses` | Ordered description-only responses 409 then 202 |
| `declared-422-suppresses-automatic` | A description-only integer 422 between those responses |
| `declared-4xx-suppresses-automatic` | A description-only `4XX` between those responses |
| `declared-default-suppresses-automatic` | A description-only `default` between those responses |

Four parity cases, four construction observations and 24 GET actions: eight
document requests, four valid required-query requests, four missing required-query
requests, four malformed required-query requests and four final state requests.
There are six actions per case and 80 selected action observations plus four
construction observations. There is no fault case or new hook.
All four construction phases and all 24 action phases select ordered warnings
through the existing runner capture flag.

The factory accepts positional `(factory_input, event_trace)` under schema9.
It creates a fresh FastAPI application per case. A single schema-visible async
endpoint requires an ordinary `int` query parameter, returns a JSONResponse and
has `response_model=None`. Additional responses contain only nonempty
descriptions. Two schema-excluded async helper endpoints return the public
`app.openapi()` result and the complete user journal. Workload code depends on
declared response inputs, never the case ID.

## Pinned source contract

Evidence is local FastAPI0.141.1, Python3.12.13, Pydantic2.13.4/core2.46.4 and
Starlette1.6.0. Starlette-RS remains the immutable sibling pin b4c8a65; no sibling
behavior or threading repair is proposed here.

- `fastapi/openapi/utils.py:332-343` collects route parameters. The required
  integer query is sufficient to enter the automatic validation-response
  decision; no request body or dependency shape is needed.
- `fastapi/openapi/utils.py:416-473` inserts the primary response.
  Lines474-516 merge declared responses in dictionary insertion order, convert
  their keys to strings, and canonicalize the default key.
- `fastapi/openapi/utils.py:517-538` runs afterward. Automatic validation422 is
  added only when parameters/body exist and none of `422`, `4XX`, `default` is
  present. The automatic branch adds the validation schema definitions. Whole
  response documents retain observable status order and definition presence.
- `fastapi/openapi/utils.py:667-679` sorts component schema names and finalizes
  through the public OpenAPI model/encoder. Exact wire bytes remain selected;
  the recipe does not sort or project away status, schema or document ordering.
- `fastapi/routing.py:1038-1054` accepts ordinary response records and creates
  extra model fields only for a truthy model. These description-only records
  avoid extra field adapters. `fastapi/utils.py:26-41` also recognizes the range
  and default status spellings for response-body eligibility.
- `fastapi/routing.py:481-491,751-755` validates inputs before endpoint execution
  and raises RequestValidationError for errors. The default public handler at
  `fastapi/exception_handlers.py:20-26` returns the actual422 JSON response.
  Documentation suppression does not configure a replacement validation handler.
- `fastapi/applications.py:1070-1103` exposes normal `app.openapi()` generation
  and caching. The second document action observes this public method without
  reading or changing its cache.
- `fastapi/applications.py:1160-1164` exposes async `FastAPI.__call__`.
  The public ASGI wrapper invokes that application object for every request,
  including the final state request.

The recipe cites the existing additional-response, query-parameter and error
handling documentation and the relevant test paths as provenance. Their test
implementations or stored outcomes have not been copied into the workload.

## Observations and determinism

Each request selects `http_response` status/ordered headers/raw body,
`asgi_send` message types with ordered comparison, and the actual
`application_error.exception`. Both document actions additionally select the
empty OpenAPI JSON pointer, preserving the whole live document.

`capture_warnings: true` is declared on each construction observation and each
HTTP action, following the schema9 locations. The existing runner sidecars
retain ordered warning category module/qualname, unchanged message, existing
filename representation and line number, including warnings from a failed
construction or raised request. No workload warning filter or custom warning
journal is added, and no comparator/normalizer is changed. Static selection
does not claim that a particular phase emits any warning.

The ASGI wrapper records every send field without dropping `more_body`, headers,
body, optional keys or order. Bytes use a lossless hex projection; tuple/list
container kinds stay distinguished. The final state request returns all earlier
setup, request, endpoint, public-document and raw-send entries, plus exact
uncaught error module/qualname/message. It excludes its own recording to avoid
recursive journal growth, and its complete response remains selected by the
runner. No timestamps, addresses, thread IDs or raw callable reprs are projected.

The public document endpoint also records the actual response-status key order,
component-schema name order and top-level key order. These are live public
document observations rather than prescribed values. The endpoint journal
distinguishes accepted requests from validation-rejected requests without
substituting a custom validation exception handler.

## Candidate public API mapping

The same mapping applies to all four cases. Preserve existing classifications;
do not create private/public promotions or new normalization rules.

| Existing candidate operation | Direct public use and observations |
|---|---|
| `fastapi.FastAPI` | Root constructor import, construction outcome/error and public application requests |
| `fastapi.applications.FastAPI` | Canonical constructor alias, same construction/application observations |
| `fastapi.applications.FastAPI.__call__` | Actual wrapper call for every request, exact HTTP/error/warning observations and complete prior raw sends |
| `fastapi.applications.FastAPI.get` | Saved decorator creation/attachment, required query validation, documented responses and complete HTTP/OpenAPI observations |
| `fastapi.applications.FastAPI.openapi` | Direct helper endpoint call plus docs generation, whole document/raw bytes and public document-order journal |
| `fastapi.responses.JSONResponse` | Returned endpoint/helper responses, status/headers/body and complete prior raw-send projection |

Validation default-handler internals are source evidence for the observed
FastAPI registration/request contract; the workload neither imports nor calls
them directly. It does not call `fastapi.openapi.utils.get_openapi` directly.

## Admission and execution boundary

Static source inspection of current native source identifies two independent
limitations: `fastapi-rs/src/openapi.rs:349-361` inserts automatic422 before
additional response merging, and
`fastapi-rs/src/application_runtime.rs:5402-5406` rejects noninteger response
status keys during decorator attachment. This is a prospective diagnosis, not
a live result. The first two cases use the currently accepted description-only
integer records. The wildcard/default cases deliberately keep the public
declarations and exact construction class/message/outcome. A target construction
failure must remain a parity mismatch; it must not be swallowed, called a fault,
or represented as action execution. Source construction errors would likewise
be actual observations and would block the proposed source-reachability gate.

Before any implementation claim, parent must review/admit unchanged files and
metadata, regenerate with the canonical commands, then require all four source
constructions and 24 actions to complete in isolated identity-checked processes.
Only then run unchanged-target diagnosis. Preserve artifacts and separate
construction failures from completed action comparisons. No fault build is
required because ordinary public inputs reach every selected behavior.

The proposal does not claim response-model adapters, arbitrary response content,
headers/links/extensions, lowercase status normalization, include/router maps,
optional or body-only validation, dependency flattening, primary status422,
validation definitions colliding with user schema names, custom error handlers,
or generic OpenAPI model coercion beyond the complete observed document. Those
need independent inputs. The current retained-field three-case wave and prior203
regression gates are separate evidence.

## Static admission

Canonical `scripts.build_parity_inputs.read_recipe` and workflow@9 schema checks
passed for this inactive recipe. YAML uses whole-value aliases only, no merge
keys. AST/source-evidence/count/selector checks and repository-config Ruff checks
are recorded alongside final hashes. Stripping only the warning-selection flags
reproduces the original v1 parsed recipe exactly. Workload bytes and four-case,
24-action stimulus counts are unchanged. No workload import, application execution,
source/target process, parity run, build or install is performed for this draft.
