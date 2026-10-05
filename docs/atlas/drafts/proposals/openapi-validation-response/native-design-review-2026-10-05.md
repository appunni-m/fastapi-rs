# Inactive automatic-422 and additional status-key design

Date: 2026-10-05. Source-only design review, not native implementation or live
evidence. No active source/input/metadata, helper, sibling or native binary was
changed or loaded. No app/model import, build, unit framework or parity stage
was run. The already-admitted graph correction and its gates remain separate.

## Input binding and admission

The inactive files remain under
`docs/atlas/drafts/proposals/openapi-validation-response/`:

| File | SHA256 |
|---|---|
| openapi_validation_response.py | 9f10522043994cc9864a1f77efe1d9eec6056e55abcc863cfcf139e52f3e6130 |
| openapi-validation-response.yaml | 4162be8ca5936b1fe8849845bc8e5978574a829250fabe1b567a3afa31ec0334 |
| review-plan.md | 1f859e84f347cb97878b9c618931ca63996a1ba503a012f477911e49f3914f77 |
| independent-review.md | 40d02bdd88c96d8ab0e2fa6a3d54eea4084c49134579040a56cc292b640a882e |

Four input distinctions under `fastapi.openapi-validation-response.` are
`automatic-after-declared-responses`, `declared-422-suppresses-automatic`,
`declared-4xx-suppresses-automatic`, and
`declared-default-suppresses-automatic`. They use unsorted 409/202 description
records and optionally an intervening integer 422, literal 4XX or literal
default. They contain no model entries. Counts stay four parity constructors,
24 GET actions, 80 action observations, four construction observations and
28 ordered-warning capture phases. No fault is justified: public declarations
and ordinary requests reach these branches.

The positional input-only factory never receives a case ID. It registers a
schema-visible async route requiring an int query parameter and returning
JSONResponse with response_model=None. Saved-decorator creation/attachment,
docs/public openapi calls, valid/missing/malformed queries and final journal are
ordinary public inputs. Description-only range/default declarations therefore
do not require response-field adapters. The unchanged input review/canonical
schema/Ruff receipt is historical static admission, not app execution.

Required next gate: admit/review exact files and existing operation links,
regenerate canonically, require all four live source constructors and 24 actions
to complete, then preserve unchanged-target diagnosis before implementation.
A target construction error must remain a parity mismatch with planned actions
not_run; do not count those actions as executed or relabel it as a fault.

## Exact source stages

Pinned FastAPI 0.141.1 source is authoritative. models.py SHA256 is
`b708c95867fa95c29125981a6427274344de9f584385cc822e06ebeed5c83f7d`;
openapi/utils.py SHA256 is
`81dcea2b8784bb1a68426c99c9525f44634b583916a894a3c7d924a72886f527`.

### Attachment and field ownership

`routing.py:1015–1037` retains the response map, ordinary metadata and unique ID;
only the primary status_code IntEnum is normalized to int there. Additional
keys are not normalized at this point. At 1038–1054, source asserts each response
is a dict, reads model and tests its truth value. Only a truthy model triggers
body eligibility, the `Response_{raw_status}_{unique_id}` formatted name, and a
serialization-mode field. Description-only records have no status conversion or
field construction. The response_fields map uses the original keys; original
responses and independently constructed context fields have separate owners.

`fastapi/utils.py:26–40` body eligibility is:

1. None returns true.
2. Raw membership in default/1XX/2XX/3XX/4XX/5XX returns true.
3. Otherwise call int(raw_status); allow >=200 except 204/205/304.

The membership is case-sensitive. It is distinct from documentation key
canonicalization. For example, description-only DEFAULT or lowercase 4xx can
reach documentation generation, whereas a truthy model with either spelling
does not pass the raw membership branch and int conversion can raise. Known
ranges, including 1XX, are allowed by this source helper. Do not impose a generic
HTTP-body rule on its range branch. There is no u16/upper numeric limit in the
additional-response field check. Bool/IntEnum/numeric strings and arbitrary
ordinary key protocols are not given an integer-only attachment rejection by
source; broader evidence for those inputs remains absent here.

The body assertion and name use the original formatted object, not its future
document key. Actual int/format/model truthiness errors must propagate at their
source stage. A false model skips these conversions and creates no field.

### OpenAPI response merge

`openapi/utils.py:416–473` first creates the primary response, description and
eligible content. Lines 474–516 then iterate extras in declaration order:

- deepcopy the response record and remove model;
- obtain `str(raw_status).upper()`, changing DEFAULT to lowercase default;
- setdefault the resulting response key (replacement does not move an existing
  key's position), then assert the copied record is a dict;
- look up the field by its original key, get its mapped schema when present,
  and recursively merge that schema into copied content;
- evaluate the range-description lookup using a second str(raw_status).upper(),
  or http.client.responses.get(int(raw_status)), before choosing the description;
- choose copied description or existing primary description or status text or
  Additional Response, deep-update the response, then assign description.

The second conversion/fallback is evaluated even when a nonempty explicit
description is present. Arbitrary keys cannot be validated or normalized early
without changing error/callback timing. `utils.py:105–118` deep_dict_update
recurses into matching dicts, concatenates matching lists and otherwise replaces
values. Overlapping primary keys, schema sibling merges and other record fields
are more than a shallow description/schema overwrite.

The current proposal uses only descriptions, so it positively observes key
order and suppression rather than full recursive response metadata merging.
Keep the existing explicitly restricted description/model policy separate from
this status-key slice; do not claim arbitrary headers/content/links/extensions,
empty descriptions or fallback descriptions from these four cases.

### Automatic validation response

At `openapi/utils.py:332–343`, all_route_params is the flattened path/query/
header/cookie field list from the dependency graph. At 517–538, after extras,
source adds automatic 422 iff that list is nonempty OR body_field is present,
AND none of the actual merged response keys 422, 4XX, default exists. Requiredness
is not a condition. The primary response can itself supply 422; an explicit
primary status flag is not the right suppression test, including where the
response class's default status supplied the key.

Insertion comes after every declared extra. The source adds its canonical
ValidationError/HTTPValidationError definitions only on that branch. The local
get_openapi_path definitions map starts empty at 323; its group guard tests
ValidationError in that local map, then inserts both definitions. Caller
get_openapi at 646–647 updates the global definitions with path definitions,
and 668–669 sorts names. A global schemas.entry(...).or_insert(...) is not that
collision policy: it can retain a user-generated definition which source later
overwrites. The four description-only cases have no user definitions, so they
cannot prove this collision branch. A future implementation should retain the
route-local/update model or explicitly bound that retained gap, rather than
silently substitute a global membership guard.

Default request validation is independent of these documentation records.
`routing.py:481–491,751–755` and `exception_handlers.py:20–26` produce the real
RequestValidationError/422 response before endpoint execution. Declaring 422,
4XX or default changes documentation suppression, not that handler.

## Native seam and prospective minimum

No Rust patch is proposed here before the source-first gate. The relevant
existing source locations, unchanged by the private graph's finalization, are:

| Native type/function | Needed bounded correction or retained condition |
|---|---|
| application_runtime::AdditionalResponseField | Replace attachment-time status String with an owned original Py reference; clone_ref must retain it alongside response/field owners. This avoids new early conversion and preserves field name/raw key semantics. |
| build_additional_response_fields | Remove integer/bool-only key rejection. Assert response dict, retain existing declared metadata policy, test model, run raw source body eligibility only for truthy models, then construct field with original formatted key. |
| additional_response_openapi | Derive the document key in the OpenAPI stage, before extra-field schema mapping as source does. Preserve Py string/key protocols if keeping generic key behavior; canonicalization is str→upper→DEFAULT-to-default, not integer parsing or arbitrary lowercasing. |
| OpenApiAdditionalResponse | Carry an owned canonical Python key if protocol fidelity is intended, rather than prematurely forcing Rust String. A simpler String-only projection retains subclass callback/identity gaps and must not be described as their fix. |
| RouteResponseFields/Input/state and include publication | Preserve current ordered fields and atomic whole-branch publication. Clone raw status/response refs under short borrows, execute model/status callbacks and dispose failed/retired owners outside app/cache borrows. No new field cache is needed. |
| openapi::openapi_document | Merge extras first, then test merged PyDict membership for 422/4XX/default. Remove the primary status!=422 surrogate. Insert automatic response and definition group only on the actual condition, after extras. |
| CallablePlan::has_openapi_parameter_inputs and operation.validation_parameters_present | Required int query reaches the bit correctly. Source uses flattened field count, not any declared input: empty query/header BaseModels, nested dependency flattening and body-only cases remain separate positive gates. |
| schema helpers / private OpenAPI graph / existing encoder | Keep final model/Any selection, alias/exclude-none encoding, schema definitions/order and automatic response data. Do not add another wire-order visitor, normalizer or expected document. |

The raw-key choice is production declaration handling, not a whitelist based on
the four input IDs. Normal native comparisons and Python public value APIs can
implement these stages safely; no original runtime import, Python helper/eval,
unsafe, blanket warning suppression or class-name/route-shape dispatch is needed.
The current primary HTTP status u16 representation is a separate boundary and
need not be broadened to document additional range/default keys.

For the current supported description/model subset, no full deepcopy or
deep_dict_update public support claim is justified by these cases. If future
code retains copied full records to implement that broader contract, add an
independent input gate before changing the restricted policy. Likewise raw
key ownership alone does not emulate mutable hash changes in source's separate
response_fields dict or all str/upper/format/int callback ordering across the
existing operation snapshot architecture; those protocol histories remain
separately unproved.

## Public mappings and exact observations

All four cases use existing constructor/root alias, FastAPI.get,
FastAPI.__call__, FastAPI.openapi and JSONResponse operation candidates. Actual
imports are public FastAPI and JSONResponse. The canonical constructor alias
does not become a new independent identity observation. The default validation
handler/OpenAPI internals are source evidence, not imported/called operations.
There is no Request injection, Pydantic Field import, APIRouter/include call,
exception-handler registration or direct get_openapi invocation in this workload.
Do not add those fixture links or public/private promotions.

All HTTP status/ordered headers/raw body, ASGI message types and application
errors stay exact; both document actions retain the whole JSON document, with
raw bytes separately protecting key order. The final state exposes all prior
setup/request/endpoint/document and lossless raw-send records, including optional
send fields, bytes and container kinds. Complete ordered warning sidecars stay
selected at construction and every action. No normalization, expected status,
prescribed schema, selector reduction or fault hook is needed.

Next measured claims require source4/24, preserved unchanged-target receipt,
reviewed native delta, actual native import, exact four-case fresh comparison
and the unchanged full regression corpus. Broader key protocols, model field
range cases, response overlap/recursive merging, 422 definition collisions,
optional/body-only/empty-model validation, includes, custom handlers and mutable
schema history remain separate input/design gates. This document does not
predict comparison results or close any of them.
