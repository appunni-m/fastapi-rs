# Independent inactive automatic-422 input review

Date: 2026-10-05. Reviewer: `/root/dependency_records_runtime` (Sol).

Scope is the TMP-only proposal, source facts, canonical recipe/schema loader,
AST, and repository-config Ruff admission. No workload was imported, factory
called, application run, native binary loaded, builder invoked, active file
edited or parity outcome produced. This proposal remains separate from the
active retained-response-field three-case gate.

## Version chronology

Original v1 identities supplied by the parent and independently confirmed:

| File | SHA256 |
| --- | --- |
| `openapi_validation_response.py` | `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130` |
| `openapi-validation-response.yaml` | `3011a159d5f2bc478d14424e8c6854a1b0424078ef7551a0bda7f4480c36ed58` |
| `review-plan.md` | `309c07e962db543678a8d56c0fe4aa45ef630dde1cd1bdbf2ebc389756ea51b8` |
| Canonical materialized v1 JSON | `c1e17d7228cb2f419cebbdef4eb656a7c354eedc0912ad58e464d3297e6de1a1` |

Reviewed v1 bytes and the static check receipt are retained in
`independent-review-v1/`. The v1 source/schema/AST/Ruff checks passed. Two
observation/mapping omissions were sent to the parent and author:

1. V1 selected no warning sidecars at construction or any action and contained
   no alternative warning journal. Schema9 warning capture is opt-in:
   `scripts/parity/worker.py:728-748,973-987,1249-1264`; comparator
   `scripts/parity/comparator.py:404-435,469-495` compares the complete ordered
   sidecar only when `capture_warnings` is true. Absence is not full warning
   parity. Parent requested true at all four constructions and 24 actions.
2. V1's public API candidate table omitted
   `fastapi.applications.FastAPI.__call__`, although the public wrapper calls
   the application at workload lines65/83. Parent requested that existing
   reviewed operation candidate; no private handler promotion is needed.

V2 identities were independently read back after the author's correction:

| File | SHA256 |
| --- | --- |
| Unchanged workload | `9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130` |
| Revised recipe | `4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334` |
| Revised plan | `1f859e84f347cb97878b9c618931ca63996a1ba503a012f477911e49f3914f77` |
| Canonical materialized v2 JSON | `0ef0311b4fc9930eb2faeb442bc28742f0f3d3bd0a0f6bae753dd684ed7b2dc9` |

V2's only parsed recipe changes are `capture_warnings: true` at all 28 phases.
Removing exactly those flags reproduces the independently archived v1 recipe.
The workload is byte-identical. Plan additions describe the warning sidecars,
version chronology and actual `FastAPI.__call__` use, with pinned public source
at `applications.py:1160-1164`. Canonical recipe/schema validation passed again.
Both v1 findings are resolved; no further static input or source-reachability
blocker was found in the bounded four-case proposal. This is clearance for
parent admission/source-first execution, not measured compatibility.

## Input and reachability review

Four fresh applications take ordinary declared response maps. The cases differ
only by their input declarations: 409 then 202; insertion of integer 422;
insertion of `4XX`; insertion of `default`. The workload never receives or
checks a case ID. It imports only the public FastAPI constructor and public
JSONResponse plus ordinary standard-library types. It does not import source
tests/runtime helpers or inspect route/cache internals, module locations,
backend versions, target availability, private framework attributes or build
identity. Public exception type module/qualname and messages are observed;
these are not private framework peeks.

The schema-visible route is async, has an ordinary required integer query and
explicit `response_model=None`, and returns a Response object. Descriptions are
nonempty and contain no models/content/extensions. Schema-excluded `/document`
and `/state` routes use the same public decorator API and return JSONResponse.
The saved decorator creation/attachment is ordinary public input, including
for wildcard/default statuses. No constructor failure is caught or replaced.

There are four construction observations and 24 GET actions, six per case:
docs; valid query; missing query; malformed query; public document; final state.
Totals are eight whole-document requests, twelve query requests, four state
requests and 80 selected action observations. Action IDs are unique within
each case; case IDs are unique. Whole-value YAML anchors introduce no merge
keys, expected outputs or conditional execution.

## Exact public observations

Every action selects actual HTTP status, ordered headers and raw body with
exact comparison; ordered ASGI message types; and application exception. Both
document actions additionally select the empty JSON pointer (whole document).
The whole raw HTTP body protects wire key order even where a parsed document
comparison has ordinary object-map semantics. No reduced schema/status subset,
sorting or new normalization hides document fields or bytes.

The wrapper losslessly journals every earlier send field/key and field order,
bytes as hex, tuple/list distinction and ordered header values. It retains
optional `more_body` presence and the complete sent body. The final state
response exposes the complete earlier setup/request/endpoint/document/error/
send journal. `/state` itself is excluded from recursive journaling but its
actual status/headers/body/message types/exception remain selected. The
workload records public document response-key/component/top-level order as
additional live data, not predetermined values. No timers, thread identities,
object addresses, nondeterministic callable representations or filtered
messages are projected.

V2 selects the runner's complete
ordered category/message/location sidecars, including warnings emitted before
an error, without workload filters or message reduction.
No expected source error or status is encoded in the recipe.

## Pinned source contract and isolated gaps

FastAPI 0.141.1 source `openapi/utils.py:332-343` collects query parameters;
the ordinary required query reaches the automatic 422 decision.
`utils.py:416-473` builds the primary response; 474-516 merges declared responses
in input order and canonicalizes `default`; 517-536 then inserts automatic 422
and validation definitions only when no 422/4XX/default key exists. The status
range/default descriptions are supported at 78-85, and `fastapi/utils.py:26-40`
recognizes range/default body-eligibility keys. `routing.py:1038-1054` creates no
extra model adapter for these description-only records. Final definition names
are sorted at `openapi/utils.py:668-669` and the public model/encoder runs at679.

Documentation suppression does not install a request-validation handler.
`routing.py:481-491,751-755` rejects invalid inputs before endpoint execution;
`exception_handlers.py:20-26` supplies the default actual422 JSON response.
The valid/missing/malformed requests and endpoint journal expose this distinction
through public behavior. They do not directly call or promote those handlers.
`applications.py:1070-1103` is the public `openapi()` cache/generation boundary.
The second document call observes reuse without peeking at `openapi_schema`.

The two current native gaps remain separate:

- `openapi.rs:349-359` inserts automatic 422/definitions before declared extra
  responses. A declared integer 422 can overwrite its description while
  retaining automatic content/definitions; source suppresses the automatic
  branch. This proposal observes the full live document instead of assuming
  merely a response-key mismatch.
- `application_runtime.rs:5402-5406` rejects noninteger response-status keys at
  attachment. Wildcard/default constructor errors must remain ordinary parity
  mismatches. Worker `worker.py:1265-1295` records actual constructor errors
  and planned actions as `not_run`; that does not count as HTTP execution or
  become a target-only fault. No skip or substitution is allowed.

Static inspection does not establish source or target support. Admission must
require all four source constructors and all 24 planned source actions to
complete, then preserve the unchanged-target diagnosis including any ordinary
constructor failures. All source-evidence files cited by the recipe exist.
Independent names, descriptions, scalar input values and journal logic are
authored stimuli; no upstream test implementation or stored result is copied.

## Reviewed candidate mappings

These are prospective mappings to existing reviewed public operations, not
new support or alias-identity evidence:

| Candidate | Actual use / evidence |
| --- | --- |
| `fastapi.FastAPI` | Root constructor binding, actual construction/errors |
| `fastapi.applications.FastAPI` | Existing canonical constructor alias; no new identity comparison |
| `fastapi.applications.FastAPI.get` | Public saved decorator creation/attachment and route options |
| `fastapi.applications.FastAPI.__call__` | Explicit wrapper invocation and actual complete HTTP/error/send observations |
| `fastapi.applications.FastAPI.openapi` | Public document call plus docs entry, complete document/wire observations |
| `fastapi.responses.JSONResponse` | Public returned response constructor and actual response/sends |

`get`/`openapi` evidence is pinned application/routing/OpenAPI source plus the
recipe's additional-response, query and error documentation. `__call__` uses
the existing application invocation overlay and observed validation pipeline.
JSONResponse remains the pinned sibling-owned reexport. Default validation
handlers and OpenAPI internals remain source evidence only; the workload does
not directly call public `fastapi.openapi.utils.get_openapi`, install handlers,
or use private Default/ModelField APIs.

## Static admission and remaining bounds

Canonical `scripts.build_parity_inputs.read_recipe` and schema@9 validation,
factory positional AST, case/action uniqueness, complete selectors/evidence,
and repository-config Ruff lint/format check passed for v1. No-cache Ruff
commands did not import the workload. Full `load_workflow` admission was not
called because it requires admitted repository-local JSON/workload paths;
the proposal deliberately names future inactive paths.

V2 canonical/schema and narrow byte/parsed-delta checks are recorded in
`independent-static-review-v2.json`. The unchanged workload retains its passed
Ruff/AST result. Counts remain 4 parity/4 construction/24 GET/80 action
observations, plus 28 selected ordered warning sidecars. No source/application
execution occurred and no observed source/target outcome is substituted here.

Remaining unselected contracts include model adapters, response content/header/
link/extensions, status coercion/lowercase spellings, primary 422, body-only or
optional validation, included contexts, dependency flattening, shared-name
collisions, custom validation handlers and full OpenAPI model unions/coercions.
Current three-case retained-field live results and earlier 203 cases remain
separate gates. No active input, metadata, source or comparator was edited.
