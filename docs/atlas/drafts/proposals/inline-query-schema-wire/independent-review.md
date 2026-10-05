# Independent inactive inline-query wire review

2026-10-05. No concrete input/admission blocker found by static review. This
does not establish source reachability or target compatibility. Active d508878
measurement sources, metadata, inputs and native artifacts were untouched; no
workload, application or native module was imported/executed, and no build or
parity stage was run.

## Frozen files and static checks

| Proposal file | Verified SHA256 |
|---|---|
| `inline_query_schema_wire.py` | `016c09632284d0c845f5c13554ccad9865884560cbf26ddc7a7bc384476159ef` |
| `inline-query-schema-wire.yaml` | `316011379f94c5084c210aa7dc1d8e28af2a620df35f8b13a028c7552e7811bc` |
| `review-plan.md` | `446052fd97849438c3b3bc72676b0dc3f29b66d4fbfdc1134501fc1d5dd0797a` |

Independent canonical `read_recipe`/schema-9 loading and AST checks pass. The
factory has the positional `(factory_input, event_trace)` contract. Whole-value
YAML aliases are valid; there are no merge keys. Counts are exactly two parity
constructors, eight GET actions, 28 action observations and ten warning-capture
phases. All declared source evidence files exist. Prospective active workload
and recipe paths remain absent. Canonical future input bytes hash to
`3526e6b55176663e566ae1495c8b5e3ce9779a98cbfe9aaec10750b2e4dbd9b1`;
no active materialization was performed.

Repository-config Ruff lint and format checks both return 0, with cache writing
disabled. No proposal bytes were changed. Independent static receipt is
`/private/tmp/fastapi-rs-inline-query-schema-wire-independent-static-review.json`,
SHA256 `96f0b203b17dd91e2ff7354185ebd08baa91dbc4599559dc10560e063d742b26`.

## Public input independence and source grounding

The factory selects public declaration placement only. Neither recipe case IDs
nor implementation identities reach workload control flow. Both signatures use
the same five independently named primitive parameters: nonzero integer defaults
13/29, empty string and nullable int/str defaults None. The dependency variant
passes an ordinary async callable through a retained public Depends marker;
the direct variant declares endpoint parameters. There is no Query/Field/model
hook, serializer, expected schema key sequence, source snapshot, private route/
adapter/cache inspection, backend lookup or copied upstream test body. Returned
JSONResponse and explicit `response_model=None` avoid response-model work.

The five source hashes in the plan were independently verified against the
pinned checkout: dependencies/utils.py `13693375…`, _compat/v2.py `b031b28b…`,
openapi/utils.py `81dcea2b…`, encoders.py `4cc09230…`, and openapi/models.py
`b708c958…`. Source references support this bounded shape:

- `dependencies/utils.py:491-538` carries ordinary defaults into inferred Query
  FieldInfo and field construction; `550-565` appends fields. `get_flat_params`
  at `169-198` and OpenAPI field collection at `utils.py:551-583` retain direct
  and dependency-owned inputs; OpenAPI parameter assembly at `160-231` embeds
  their mapped schemas in declaration traversal order.
- `_compat/v2.py:141-167` reconstructs field metadata/attributes before the
  retained TypeAdapter. Shared generation at `285-336` precedes mapped schema
  lookup/title application at `254-282`. The proposal selects resulting bytes
  without prescribing default/None encoding or moving dictionary keys itself.
- `openapi/utils.py:679`, `openapi/models.py:425-427` and the recursive encoder
  determine final wire values/order. The final PathItem|Any union does not
  justify a global model-field-order assumption. The legacy diagnosis remains
  historical motivation, not expected results for these new declarations.
- Public `FastAPI.openapi` returns its cached document under stable route
  version at `applications.py:1084-1110`; docs invokes it at `1116-1118`. The
  workload compares objects returned by that public method only. It does not
  inspect or change `openapi_schema` or private cache state.

## Exact selections and journal boundary

Every action selects status, ordered headers and full raw body exactly; ASGI
message types use ordered comparison, and actual application exception is exact.
Both docs actions also select the whole structural document. Raw bytes protect
map order which structural JSON equality alone does not. Construction and all
actions select the existing full ordered warning sidecars; there is no custom
filter, warning normalization or assertion that a phase emits no warning.

Both endpoint responses expose injected values/types, the public document and
live journal. The wrapper preserves prior send keys, byte hex, tuple/list shape,
order and exceptions without dropping optional ASGI fields. The final endpoint
body includes the earlier three requests' send/exit records and its own current
endpoint/document entries. Its own send/exit cannot be represented recursively
inside that body; those responses still have directly selected HTTP bytes and
message types. This is correctly bounded in the plan, not a claim of a complete
post-final-action journal. Ordinary constructor/request errors must retain
actual outcomes and any subsequent unrun actions in future receipts.

## Existing API mappings and required gates

The recommended 14 case-operation links use eight existing reviewed IDs:

| Case | Existing operation IDs |
|---|---|
| Both | `fastapi.FastAPI`, `fastapi.applications.FastAPI`, `fastapi.applications.FastAPI.__call__`, `fastapi.applications.FastAPI.get`, `fastapi.applications.FastAPI.openapi`, `fastapi.responses.JSONResponse` |
| Dependency only | `fastapi.Depends`, `fastapi.param_functions.Depends` |

All eight IDs exist in current metadata. Root/canonical alias links retain the
existing policy and do not become separate identity probes. Importing Depends
in the direct case does not justify a direct-case Depends link. No Request,
Pydantic Field/private ModelField, get_openapi, APIRouter/include or exception
handler registration link is exercised. Generated full-case selector provenance
does not establish every linked operation or unselected branch individually.

Admission remains inactive until current measurements close. Then preserve
unchanged files and reviewed existing-operation links, regenerate canonically,
require two successful source constructors/eight completed actions and retain
unchanged-target diagnosis before implementation. None/default serializers,
aliases/titles/metadata, references/shared input-hook batching, nonserializable
defaults, body/header/cookie/path fields, namespace/mutable-adapter history and
broader cache mutation remain separate gates. No fault hook or comparator change
is justified by these ordinary public inputs.
